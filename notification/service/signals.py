from service.models import Mailing, Client, Message
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from service.utils import send_messages


@receiver(pre_save, sender=Mailing)
def del_message(instance, **kwargs):
    # перед обновлением будут удаляться старые, при условии, что сообщения не были отпралены
    old_mailing = Mailing.objects.filter(id=instance.pk).first()
    if old_mailing is not None:
        Message.objects.filter(mailing_id=old_mailing.pk, status='waiting').delete()
        print('delete')

@receiver(post_save, sender=Mailing)
def signal_message(sender, instance, created, **kwargs):
    # при обновлении(изменении тега, кода, текста) и создании рассылки будут создаваться новые сообщения
    clients = Client.objects.filter(mobile_code=instance.mobile_code, tag=instance.tag)
    data_set = {
        'clients': clients,
        'client_set': {}, # client_id: mesage_id
    }
    for client in clients:
        mesage = Message.objects.create(status="waiting", client_id=client.pk, mailing_id=instance.pk)
        data_set['client_set'][client.pk] = mesage.pk
    send_messages(instance.id, data_set)
    print(data_set)

